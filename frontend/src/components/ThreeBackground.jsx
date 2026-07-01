import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Float, Points, PointMaterial } from '@react-three/drei'
import * as random from 'maath/random/dist/maath-random.esm'

function Particles() {
  const ref = useRef()
  // Generate 500 random points in a sphere
  const sphere = useMemo(() => random.inSphere(new Float32Array(500 * 3), { radius: 1.5 }), [])

  useFrame((state, delta) => {
    ref.current.rotation.x -= delta / 10
    ref.current.rotation.y -= delta / 15
  })

  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <Points ref={ref} positions={sphere} stride={3} frustumCulled={false}>
        <PointMaterial
          transparent
          color="#8b5cf6"
          size={0.005}
          sizeAttenuation={true}
          depthWrite={false}
        />
      </Points>
    </group>
  )
}

function Geometry() {
  const mesh = useRef()

  useFrame((state, delta) => {
    mesh.current.rotation.x += delta * 0.1
    mesh.current.rotation.y += delta * 0.15
  })

  return (
    <Float speed={1.5} rotationIntensity={1} floatIntensity={2}>
      <mesh ref={mesh} scale={2}>
        <icosahedronGeometry args={[1, 1]} />
        <meshBasicMaterial color="#4f46e5" wireframe opacity={0.15} transparent />
      </mesh>
    </Float>
  )
}

export default function ThreeBackground() {
  return (
    <div className="fixed inset-0 z-[-1] bg-slate-950">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent to-slate-950/80 z-[1] pointer-events-none" />
      <Canvas camera={{ position: [0, 0, 5], fov: 60 }} gl={{ antialias: false, alpha: false }}>
        <color attach="background" args={['#020617']} />
        <Particles />
        <Geometry />
      </Canvas>
    </div>
  )
}
